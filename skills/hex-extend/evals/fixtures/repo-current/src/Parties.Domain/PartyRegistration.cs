namespace Parties.Domain;

using Hexalith.Domains;
using Hexalith.PolymorphicSerializations;

public record PartyRegistrationState(string Id, string Name, bool Registered)
{
    public static PartyRegistrationState Initial => new(string.Empty, string.Empty, false);

    public PartyRegistrationState Apply(PartyRegistered @event) =>
        this with { Id = @event.Id, Name = @event.Name, Registered = true };
}

public static class PartyRegistration
{
    public static DomainResult Handle(RegisterParty command, PartyRegistrationState? state)
    {
        if (state is { Registered: true })
        {
            return DomainResult.Failed("Party is already registered.");
        }

        return DomainResult.Succeeded(new PartyRegistered(command.Id, command.Name));
    }
}

[PolymorphicSerialization]
public record RegisterParty(string Id, string Name);

[PolymorphicSerialization]
public record PartyRegistered(string Id, string Name);
