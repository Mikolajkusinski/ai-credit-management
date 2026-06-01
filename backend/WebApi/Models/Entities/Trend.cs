namespace WebApi.Models.Entities;

public class Trend
{
    public int Id { get; set; }
    public int ClientId { get; set; }
    public string ModelName { get; set; } = default!;
    public double Slope { get; set; }
    public string Alert { get; set; } = default!;
    public DateTime ComputedAt { get; set; }

    public Client Client { get; set; } = default!;
}
