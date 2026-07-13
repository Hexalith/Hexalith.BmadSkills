// Build-time stand-ins for the Hexalith packages so this fixture compiles offline.
// Mirrors the framework API surface; not part of the module under extension.
namespace Hexalith.Commons
{
    public static class UniqueIdHelper
    {
        public static string GenerateUniqueStringId() =>
            $"{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds():x12}{Random.Shared.NextInt64():x16}";
    }
}

namespace Hexalith.Domains
{
    public record DomainResult(bool Success, string? Error, IReadOnlyList<object> Events)
    {
        public static DomainResult Succeeded(params object[] events) => new(true, null, events);

        public static DomainResult Failed(string error) => new(false, error, []);
    }
}

namespace Hexalith.PolymorphicSerializations
{
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Struct)]
    public sealed class PolymorphicSerializationAttribute : Attribute;
}
