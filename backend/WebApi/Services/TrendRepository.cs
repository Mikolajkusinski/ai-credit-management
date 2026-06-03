using Microsoft.EntityFrameworkCore;
using WebApi.Data;
using WebApi.Models.Entities;

namespace WebApi.Services;

/// <summary>
/// EF Core writes for <see cref="Trend"/> (CREDIT-203). Keeps a single current trend per
/// <c>(ClientId, ModelName)</c> — the slope (W3−W0) and alert from the latest snapshot — updated
/// on every new snapshot (per CREDIT-401 design / contract 4.3).
/// </summary>
public class TrendRepository
{
    private readonly AppDbContext _db;

    public TrendRepository(AppDbContext db) => _db = db;

    /// <summary>
    /// Upserts one trend row per model for a client and returns the rows (with ids). Existing rows
    /// are updated in place; <c>ComputedAt</c> is refreshed to the DB default (<c>NOW()</c>) on insert
    /// and bumped to <c>UtcNow</c> on update.
    /// </summary>
    public async Task<List<Trend>> UpsertRangeAsync(
        int clientId, IEnumerable<(string Model, double Slope, string Alert)> trends)
    {
        var existing = await _db.Trends
            .Where(t => t.ClientId == clientId)
            .ToListAsync();

        var result = new List<Trend>();
        foreach (var (model, slope, alert) in trends)
        {
            var row = existing.FirstOrDefault(t => t.ModelName == model);
            if (row is null)
            {
                row = new Trend { ClientId = clientId, ModelName = model, Slope = slope, Alert = alert };
                _db.Trends.Add(row);
            }
            else
            {
                row.Slope = slope;
                row.Alert = alert;
                row.ComputedAt = DateTime.UtcNow;
            }

            result.Add(row);
        }

        await _db.SaveChangesAsync();
        return result;
    }
}
