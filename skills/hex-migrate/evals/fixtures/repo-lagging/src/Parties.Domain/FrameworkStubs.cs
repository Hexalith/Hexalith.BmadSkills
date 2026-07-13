// Build-time stand-in for the Hexalith.Commons package so this fixture compiles offline.
// Mirrors the framework API surface; not part of the module under audit.
namespace Hexalith.Commons;

public static class UniqueIdHelper
{
    public static string GenerateUniqueStringId() =>
        $"{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds():x12}{Random.Shared.NextInt64():x16}";
}
