export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const LOCATIONS = [
  "USA",
  "China",
  "Vietnam",
  "Bangladesh",
  "India",
  "Mexico",
  "Turkey",
  "Indonesia",
  "Thailand",
  "Portugal",
  "Italy",
  "Pakistan",
  "Cambodia",
  "Sri Lanka",
  "Taiwan",
  "South Korea",
] as const;

export const CERTIFICATIONS = [
  "OEKO-TEX",
  "GOTS",
  "Fair Trade",
  "ISO 9001",
  "bluesign",
  "WRAP",
  "GRS",
  "BCI",
  "SA8000",
] as const;

export const MATERIALS = [
  "Recycled Polyester",
  "Organic Cotton",
  "Bamboo",
  "Nylon",
  "Spandex",
  "Merino Wool",
  "Modal",
  "Tencel/Lyocell",
  "Hemp",
  "Coolmax",
] as const;

export const PRODUCTION_METHODS = [
  "Sublimation Printing",
  "Screen Printing",
  "Embroidery",
  "Cut-and-Sew",
  "Seamless Knitting",
  "Laser Cutting",
  "Heat Transfer",
  "Digital Printing",
] as const;

export const BUDGET_TIERS = ["budget", "mid-range", "premium"] as const;

export const SEARCH_MODES = ["auto", "manual", "hybrid"] as const;

export const SEARCH_STATUS = {
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
} as const;

export const MANUFACTURER_STATUSES = [
  { value: "new", label: "New" },
  { value: "contacted", label: "Contacted" },
  { value: "quoted", label: "Quoted" },
  { value: "negotiating", label: "Negotiating" },
  { value: "won", label: "Won" },
  { value: "lost", label: "Lost" },
] as const;

export const ACTIVITY_TYPES = [
  { value: "email", label: "Email" },
  { value: "call", label: "Call" },
  { value: "meeting", label: "Meeting" },
  { value: "quote_received", label: "Quote Received" },
  { value: "sample_requested", label: "Sample Requested" },
  { value: "note", label: "Note" },
] as const;
