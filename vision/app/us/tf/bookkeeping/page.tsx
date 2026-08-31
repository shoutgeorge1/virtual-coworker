import type { Metadata } from "next";
import TrustFirstUsPage, {
  trustFirstProductionMetadata,
} from "../../../components/trust-first/TrustFirstUsPage";

export const metadata: Metadata = trustFirstProductionMetadata("bookkeeping");

type Props = {
  searchParams: Promise<{ v?: string }>;
};

export default function USTrustFirstBookkeepingPage({ searchParams }: Props) {
  return <TrustFirstUsPage pageKey="bookkeeping" searchParams={searchParams} />;
}
