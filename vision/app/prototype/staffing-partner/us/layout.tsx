import MarketGtm from "../../../components/MarketGtm";

export default function StaffingPartnerUsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <MarketGtm surface="us" />
      {children}
    </>
  );
}
