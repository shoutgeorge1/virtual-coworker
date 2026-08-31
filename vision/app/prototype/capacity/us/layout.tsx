import MarketGtm from "../../../components/MarketGtm";

export default function CapacityUsLayout({
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
