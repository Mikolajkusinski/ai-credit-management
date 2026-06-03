using System.ComponentModel.DataAnnotations;

namespace WebApi.Models;

/// <summary>
/// The 22 input features for a single client snapshot (monitoring API contract section 3.1).
/// Validated automatically by <c>[ApiController]</c> via the DataAnnotations below; on failure
/// the configured <c>InvalidModelStateResponseFactory</c> returns an <see cref="ErrorEnvelope"/>
/// with code <c>VALIDATION_FAILED</c>. Kept separate from the legacy <see cref="PredictRequest"/>
/// so that the legacy <c>/api/predict</c> behaviour is unchanged.
/// </summary>
public class Snapshot22Features
{
    [Range(10000, 1000000)]
    public int LimitBal { get; set; }

    [Range(1, 2)]
    public int Sex { get; set; }

    [Range(1, 4)]
    public int Education { get; set; }

    [Range(1, 3)]
    public int Marriage { get; set; }

    [Range(18, 100)]
    public int Age { get; set; }

    // Payment status: -2 = no consumption, -1 = paid in full, 0..8 = months of delay.
    [Range(-2, 8)] public int Pay0 { get; set; }
    [Range(-2, 8)] public int Pay2 { get; set; }
    [Range(-2, 8)] public int Pay3 { get; set; }
    [Range(-2, 8)] public int Pay4 { get; set; }
    [Range(-2, 8)] public int Pay5 { get; set; }
    [Range(-2, 8)] public int Pay6 { get; set; }

    // Bill / payment amounts may be negative (overpayments) — no range constraint.
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
}
