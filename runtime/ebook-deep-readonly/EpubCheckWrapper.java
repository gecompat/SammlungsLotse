import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;

/**
 * Keeps the bounded output tmpfs mounted until the host has copied the report.
 * The provider command is constructed as an argument vector and never uses a shell.
 */
public final class EpubCheckWrapper {
    private static final Path OUTPUT = Path.of("/output");
    private static final int STDOUT_LIMIT = 131072;
    private static final int STDERR_LIMIT = 131072;
    private static final List<String> EXPECTED_ARGUMENTS = List.of(
        "/input/input.epub", "--json", "/output/report.json"
    );

    private EpubCheckWrapper() {
    }

    private record Capture(byte[] retained, boolean truncated) {
    }

    private static Capture drain(InputStream stream, int limit) throws IOException {
        ByteArrayOutputStream retained = new ByteArrayOutputStream(limit);
        byte[] chunk = new byte[8192];
        boolean truncated = false;
        int count;
        while ((count = stream.read(chunk)) != -1) {
            int remaining = limit - retained.size();
            if (remaining > 0) {
                retained.write(chunk, 0, Math.min(remaining, count));
            }
            if (count > Math.max(remaining, 0)) {
                truncated = true;
            }
        }
        return new Capture(retained.toByteArray(), truncated);
    }

    private static void write(Path path, byte[] value) throws IOException {
        Files.write(path, value, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    }

    public static void main(String[] arguments) throws Exception {
        if (!List.of(arguments).equals(EXPECTED_ARGUMENTS)) {
            System.exit(64);
        }
        Process process = new ProcessBuilder(
            "/opt/java/bin/java",
            "-Djava.awt.headless=true",
            "-Djava.io.tmpdir=/tmp",
            "-Xms16m",
            "-Xmx256m",
            "-jar",
            "/opt/epubcheck/epubcheck.jar",
            arguments[0],
            arguments[1],
            arguments[2]
        ).redirectInput(Path.of("/dev/null").toFile()).start();

        Capture[] captures = new Capture[2];
        IOException[] failures = new IOException[2];
        Thread stdout = Thread.ofPlatform().start(() -> {
            try {
                captures[0] = drain(process.getInputStream(), STDOUT_LIMIT);
            } catch (IOException error) {
                failures[0] = error;
            }
        });
        Thread stderr = Thread.ofPlatform().start(() -> {
            try {
                captures[1] = drain(process.getErrorStream(), STDERR_LIMIT);
            } catch (IOException error) {
                failures[1] = error;
            }
        });

        int exitCode = process.waitFor();
        stdout.join();
        stderr.join();
        if (failures[0] != null || failures[1] != null) {
            throw new IOException("provider output capture failed");
        }
        write(OUTPUT.resolve("stdout.bin"), captures[0].retained());
        write(OUTPUT.resolve("stderr.bin"), captures[1].retained());
        String marker = String.format(
            "{\"exit_code\":%d,\"stdout_truncated\":%s,\"stderr_truncated\":%s}\n",
            exitCode,
            captures[0].truncated(),
            captures[1].truncated()
        );
        Files.writeString(
            OUTPUT.resolve("complete.json"),
            marker,
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE_NEW,
            StandardOpenOption.WRITE
        );

        // Podman removes tmpfs contents when PID 1 exits. The host copies the
        // bounded evidence and then force-removes this container.
        Thread.sleep(300_000L);
    }
}
