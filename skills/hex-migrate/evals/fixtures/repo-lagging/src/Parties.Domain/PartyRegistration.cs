namespace Parties.Domain;

public class PartyRegistration
{
    public string Id { get; private set; } = string.Empty;

    public string Name { get; private set; } = string.Empty;

    public bool Registered { get; private set; }

    public void Handle(RegisterParty command)
    {
        Id = Guid.NewGuid().ToString();
        Name = command.Name;
        Apply(new PartyRegistered(Id, Name));
    }

    public void Apply(PartyRegistered @event)
    {
        Registered = true;
    }
}

public record RegisterParty(string Name);

public record PartyRegistered(string Id, string Name);
