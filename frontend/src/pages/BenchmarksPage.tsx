import { BarChart3 } from 'lucide-react';
import BenchmarkCenter from '../features/benchmark/BenchmarkCenter';
export default function BenchmarksPage() {
  return (
    <div className="page">
      <div className="page-header"><div className="page-header__title"><BarChart3 size={24} /><div><h1>Benchmarks</h1><div className="page-header__subtitle">Algorithm benchmarks and performance profiling</div></div></div></div>
      <BenchmarkCenter />
    </div>
  );
}
