namespace WebApi.Models.Entities;

public class Client
{
    public int Id { get; set; }
    public string ExternalRef { get; set; } = default!;
    public DateTime CreatedAt { get; set; }

    public ICollection<Snapshot> Snapshots { get; set; } = new List<Snapshot>();
    public ICollection<Trend> Trends { get; set; } = new List<Trend>();
}
