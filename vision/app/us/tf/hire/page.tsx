import type { Metadata } from "next";
import TrustFirstUsPage, {
  trustFirstProductionMetadata,
} from "../../../components/trust-first/TrustFirstUsPage";

export const metadata: Metadata = trustFirstProductionMetadata("us");

type Props = {
  searchParams: Promise<{ v?: string }>;
};

export default function USTrustFirstHireAliasPage({ searchParams }: Props) {
  return <TrustFirstUsPage pageKey="us" searchParams={searchParams} />;
}
