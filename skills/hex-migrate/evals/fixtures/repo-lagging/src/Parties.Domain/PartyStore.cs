namespace Parties.Domain;

using System.Data.Common;

public class PartyStore
{
    public async Task SaveAsync(DbConnection connection, PartyRegistration party)
    {
        using DbCommand command = connection.CreateCommand();
        command.CommandText = "INSERT INTO Parties (Id, Name) VALUES (@id, @name)";
        DbParameter id = command.CreateParameter();
        id.ParameterName = "@id";
        id.Value = party.Id;
        command.Parameters.Add(id);
        DbParameter name = command.CreateParameter();
        name.ParameterName = "@name";
        name.Value = party.Name;
        command.Parameters.Add(name);
        await command.ExecuteNonQueryAsync();
    }
}
