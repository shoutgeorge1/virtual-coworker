import type { Metadata } from "next";
import TrustFirstUsPage, {
  trustFirstProductionMetadata,
} from "../../components/trust-first/TrustFirstUsPage";

export const metadata: Metadata = trustFirstProductionMetadata(
  "philippines-virtual-assistants",
);

type Props = {
  searchParams: Promise<{ v?: string }>;
};

export default function USPhilippinesVirtualAssistantsPage({ searchParams }: Props) {
  return (
    <TrustFirstUsPage
      pageKey="philippines-virtual-assistants"
      searchParams={searchParams}
    />
  );
}
