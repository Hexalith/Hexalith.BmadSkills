// <copyright file="PartyRegistration.cs" company="ITANEO">
// Copyright (c) ITANEO. All rights reserved.
// </copyright>

namespace Parties.Domain;

using Microsoft.EntityFrameworkCore;

/// <summary>Registers a new party.</summary>
public static class PartyRegistration
{
    public static string NewRegistrationId()
    {
        string id = Guid.NewGuid().ToString();
        return id;
    }
}

/// <summary>Persistence context for parties.</summary>
public class PartiesDbContext : DbContext
{
    public DbSet<PartyRecord> Parties => Set<PartyRecord>();
}

public record PartyRecord(string Id, string Name);
