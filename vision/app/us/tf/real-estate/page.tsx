import type { Metadata } from "next";
import TrustFirstUsPage, {
  trustFirstProductionMetadata,
} from "../../../components/trust-first/TrustFirstUsPage";

export const metadata: Metadata = trustFirstProductionMetadata("real-estate");

type Props = {
  searchParams: Promise<{ v?: string }>;
};

export default function USTrustFirstRealEstatePage({ searchParams }: Props) {
  return <TrustFirstUsPage pageKey="real-estate" searchParams={searchParams} />;
}
