namespace Hexalith.Commons.UniqueIds;

/// <summary>Generates ULID-based unique identifiers.</summary>
public static class UniqueIdHelper
{
    /// <summary>Returns a new ULID string; the canonical id generator for all
    /// entity, aggregate, command, and event identifiers.</summary>
    public static string GenerateUniqueStringId() => Ulid.NewUlid().ToString();
}
