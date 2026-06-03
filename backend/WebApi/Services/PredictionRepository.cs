using WebApi.Data;
using WebApi.Models.Entities;

namespace WebApi.Services;

/// <summary>
/// EF Core writes for <see cref="Prediction"/> (CREDIT-203). Persists the W3 (labelled-window)
/// predictions for a snapshot — one row per model (contract open question #1 = W3 only).
/// </summary>
public class PredictionRepository
{
    private readonly AppDbContext _db;

    public PredictionRepository(AppDbContext db) => _db = db;

    /// <summary>Inserts the given predictions for a snapshot and returns them with generated ids.</summary>
    public async Task<List<Prediction>> AddRangeAsync(int snapshotId, IEnumerable<Prediction> predictions)
    {
        var rows = predictions.ToList();
        foreach (var p in rows)
        {
            p.SnapshotId = snapshotId;
        }

        _db.Predictions.AddRange(rows);
        await _db.SaveChangesAsync();
        return rows;
    }
}
