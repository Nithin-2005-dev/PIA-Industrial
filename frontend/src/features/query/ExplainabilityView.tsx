
export default function ExplainabilityView() {
  const chain = [
    'Evidence', 
    'Rule Fired', 
    'Confidence', 
    'Supporting Nodes', 
    'Alternative Paths', 
    'Final Conclusion'
  ];

  return (
    <div className="flex flex-col gap-2">
      <div className="text-sm text-muted mb-2">Select a recommendation to inspect reasoning path.</div>
      <div className="flex flex-col gap-1 pl-2 border-l-2" style={{ borderColor: 'var(--panel-border)' }}>
        {chain.map((item, idx) => (
          <div key={item} className="flex items-center gap-2 py-1">
            <div className="w-2 h-2 rounded-full" style={{ background: `hsl(${210 + idx * 10}, 80%, 60%)` }}></div>
            <span className="text-sm">{item}</span>
          </div>
        ))}
      </div>
      <button className="mt-4 text-sm w-fit bg-transparent border border-accent-blue text-accent-blue hover:bg-accent-blue hover:text-white transition-colors">
        Export Explanation
      </button>
    </div>
  );
}
