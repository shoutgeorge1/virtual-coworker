import type { Metadata } from "next";
import TrustFirstUsPage, {
  trustFirstProductionMetadata,
} from "../../components/trust-first/TrustFirstUsPage";

export const metadata: Metadata = trustFirstProductionMetadata("us");

type Props = {
  searchParams: Promise<{ v?: string }>;
};

/** Isolated hire/dedicated TF test. Live /us stays on StaffingBaselineLanding. */
export default function USTrustFirstHirePage({ searchParams }: Props) {
  return <TrustFirstUsPage pageKey="us" searchParams={searchParams} />;
}
