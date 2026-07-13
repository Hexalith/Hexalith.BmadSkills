namespace HexalithApp.Server;

/// <summary>Projection wiring: each read-model handler is registered explicitly.</summary>
public static class ProjectionSetup
{
    public static IServiceCollection AddPartyProjections(this IServiceCollection services)
        => services
            .AddSingleton<IProjectionFactory<PartySummary>, PartySummaryProjectionFactory>()
            .AddSingleton<IProjectionFactory<PartyDetails>, PartyDetailsProjectionFactory>();
}
