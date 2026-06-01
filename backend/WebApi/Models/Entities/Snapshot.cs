namespace WebApi.Models.Entities;

public class Snapshot
{
    public int Id { get; set; }
    public int ClientId { get; set; }
    public DateTime SnapshotDate { get; set; }

    public int LimitBal { get; set; }
    public int Sex { get; set; }
    public int Education { get; set; }
    public int Marriage { get; set; }
    public int Age { get; set; }

    public int Pay0 { get; set; }
    public int Pay2 { get; set; }
    public int Pay3 { get; set; }
    public int Pay4 { get; set; }
    public int Pay5 { get; set; }
    public int Pay6 { get; set; }

    public decimal BillAmt1 { get; set; }
    public decimal BillAmt2 { get; set; }
    public decimal BillAmt3 { get; set; }
    public decimal BillAmt4 { get; set; }
    public decimal BillAmt5 { get; set; }
    public decimal BillAmt6 { get; set; }

    public decimal PayAmt1 { get; set; }
    public decimal PayAmt2 { get; set; }
    public decimal PayAmt3 { get; set; }
    public decimal PayAmt4 { get; set; }
    public decimal PayAmt5 { get; set; }
    public decimal PayAmt6 { get; set; }

    public Client Client { get; set; } = default!;
    public ICollection<Prediction> Predictions { get; set; } = new List<Prediction>();
}
