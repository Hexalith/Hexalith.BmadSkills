// Build-time stand-ins for xUnit and Shouldly so this fixture compiles offline.
// Mirrors the API surface the tests use; not part of the module under extension.
namespace Xunit
{
    [AttributeUsage(AttributeTargets.Method)]
    public sealed class FactAttribute : Attribute;
}

namespace Shouldly
{
    public static class ShouldlyExtensions
    {
        public static void ShouldBe<T>(this T actual, T expected)
        {
            if (!Equals(actual, expected))
            {
                throw new InvalidOperationException($"Expected {expected} but was {actual}");
            }
        }

        public static void ShouldBeTrue(this bool actual) => actual.ShouldBe(true);

        public static void ShouldBeFalse(this bool actual) => actual.ShouldBe(false);
    }
}
