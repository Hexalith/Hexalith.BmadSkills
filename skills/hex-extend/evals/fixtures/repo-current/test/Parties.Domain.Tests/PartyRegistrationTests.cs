namespace Parties.Domain.Tests;

using Hexalith.Commons;
using Hexalith.Domains;
using Parties.Domain;
using Shouldly;
using Xunit;

public class PartyRegistrationTests
{
    [Fact]
    public void HandleRegisterPartyOnNewPartyEmitsPartyRegistered()
    {
        RegisterParty command = new(UniqueIdHelper.GenerateUniqueStringId(), "Contoso");

        DomainResult result = PartyRegistration.Handle(command, null);

        result.Success.ShouldBeTrue();
        result.Events.Count.ShouldBe(1);
    }

    [Fact]
    public void HandleRegisterPartyOnRegisteredPartyFails()
    {
        PartyRegistrationState state = PartyRegistrationState.Initial.Apply(new PartyRegistered("0000018f3c2a1b4c", "Contoso"));

        DomainResult result = PartyRegistration.Handle(new RegisterParty(state.Id, state.Name), state);

        result.Success.ShouldBeFalse();
    }

    [Fact]
    public void ApplyPartyRegisteredReturnsNewRegisteredState()
    {
        PartyRegistrationState next = PartyRegistrationState.Initial.Apply(new PartyRegistered("0000018f3c2a1b4c", "Contoso"));

        next.Registered.ShouldBeTrue();
        PartyRegistrationState.Initial.Registered.ShouldBeFalse();
    }
}
