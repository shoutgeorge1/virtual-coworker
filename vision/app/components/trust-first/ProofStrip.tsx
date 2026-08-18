export default function ProofStrip({ items }: { items: readonly string[] }) {
  return (
    <div className="tf-strip" aria-label="Company facts">
      {items.map((item) => (
        <span key={item}>{item}</span>
      ))}
    </div>
  );
}
