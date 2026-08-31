import type { Metadata } from "next";
import EmployerBookPage, {
  bookPageMetadata,
} from "../../components/EmployerBookPage";

export const metadata: Metadata = bookPageMetadata("au");

export default function AuBookPage() {
  return <EmployerBookPage market="au" />;
}
