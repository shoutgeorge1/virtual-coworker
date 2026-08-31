import type { Metadata } from "next";
import EmployerBookPage, {
  bookPageMetadata,
} from "../../components/EmployerBookPage";

export const metadata: Metadata = bookPageMetadata("us");

export default function UsBookPage() {
  return <EmployerBookPage market="us" />;
}
