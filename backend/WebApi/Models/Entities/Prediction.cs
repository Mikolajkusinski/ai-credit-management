namespace WebApi.Models.Entities;

public class Prediction
{
    public int Id { get; set; }
    public int SnapshotId { get; set; }
    public string ModelName { get; set; } = default!;
    public double DefaultProbability { get; set; }
    public string Label { get; set; } = default!;

    public Snapshot Snapshot { get; set; } = default!;
}
