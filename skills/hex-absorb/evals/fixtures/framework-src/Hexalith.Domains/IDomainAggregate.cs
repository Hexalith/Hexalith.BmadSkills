namespace Hexalith.Domains;

/// <summary>A domain aggregate is a pure function over commands and events.</summary>
public interface IDomainAggregate
{
    /// <summary>Handles a command and returns the resulting domain events.</summary>
    DomainResult Handle(object command);

    /// <summary>Applies a domain event and returns the new aggregate state.</summary>
    IDomainAggregate Apply(object domainEvent);
}
