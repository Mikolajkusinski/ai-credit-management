using Microsoft.EntityFrameworkCore;
using WebApi.Data;
using WebApi.Models.Entities;

namespace WebApi.Services;

/// <summary>
/// EF Core writes for <see cref="Client"/> and <see cref="Snapshot"/> (CREDIT-203). Each method
/// is self-contained (own <c>SaveChangesAsync</c>); an explicit DB transaction across the full
/// write is deferred to CREDIT-205.
/// </summary>
public class SnapshotRepository
{
    private readonly AppDbContext _db;

    public SnapshotRepository(AppDbContext db) => _db = db;

    /// <summary>Looks up a client by its unique business key; null when it does not exist yet.</summary>
    public Task<Client?> FindClientAsync(string externalRef) =>
        _db.Clients.FirstOrDefaultAsync(c => c.ExternalRef == externalRef);

    /// <summary>Creates a client. <c>CreatedAt</c> is left to the DB default (<c>NOW()</c>).</summary>
    public async Task<Client> CreateClientAsync(string externalRef)
    {
        var client = new Client { ExternalRef = externalRef };
        _db.Clients.Add(client);
        await _db.SaveChangesAsync();
        return client;
    }

    /// <summary>True when the client already has a snapshot on the given date (duplicate guard).</summary>
    public Task<bool> ExistsForDateAsync(int clientId, DateOnly date)
    {
        var dayStart = date.ToDateTime(TimeOnly.MinValue, DateTimeKind.Utc);
        var dayEnd = dayStart.AddDays(1);
        return _db.Snapshots.AnyAsync(s =>
            s.ClientId == clientId && s.SnapshotDate >= dayStart && s.SnapshotDate < dayEnd);
    }

    /// <summary>Inserts a snapshot and returns it with its generated <c>Id</c>.</summary>
    public async Task<Snapshot> AddAsync(Snapshot snapshot)
    {
        _db.Snapshots.Add(snapshot);
        await _db.SaveChangesAsync();
        return snapshot;
    }

    /// <summary>
    /// Reads a client's snapshots (with their predictions eager-loaded) for the history endpoint
    /// (CREDIT-204). Optionally filtered by <paramref name="from"/>/<paramref name="to"/> (the
    /// <paramref name="to"/> day is inclusive) and capped at <paramref name="limit"/>. Returns the
    /// most-recent <paramref name="limit"/> snapshots in ascending date order (oldest → newest),
    /// using the existing <c>(ClientId, SnapshotDate)</c> index.
    /// </summary>
    public async Task<List<Snapshot>> GetHistoryAsync(int clientId, DateOnly? from, DateOnly? to, int limit)
    {
        var query = _db.Snapshots
            .Include(s => s.Predictions)
            .Where(s => s.ClientId == clientId);

        if (from is { } f)
        {
            query = query.Where(s => s.SnapshotDate >= f.ToDateTime(TimeOnly.MinValue, DateTimeKind.Utc));
        }

        if (to is { } t)
        {
            var dayAfterTo = t.AddDays(1).ToDateTime(TimeOnly.MinValue, DateTimeKind.Utc);
            query = query.Where(s => s.SnapshotDate < dayAfterTo);
        }

        var rows = await query
            .OrderByDescending(s => s.SnapshotDate)
            .Take(limit)
            .ToListAsync();

        rows.Reverse(); // newest-first DB read → ascending response (left = oldest on the chart)
        return rows;
    }
}
