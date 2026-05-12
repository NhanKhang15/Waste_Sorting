import type { ReactNode } from "react";
import { useClassify } from "../features/classification/hooks/useClassify";
import ClassificationForm from "../features/classification/components/ClassificationForm";
import ImageCanvas from "../features/classification/components/ImageCanvas";
import MatchResult from "../features/classification/components/MatchResult";
import DSLEditor from "../features/classification/components/DSLEditor";
import EngineInfo from "../features/classification/components/EngineInfo";
import TokenStream from "../features/classification/components/TokenStream";
import TreeVisualizer from "../features/classification/components/TreeVisualizer";

const SectionLabel = ({ children }: { children: ReactNode }) => (
  <h3 className="text-[10px] font-bold uppercase opacity-40 mb-3 tracking-widest">{children}</h3>
);

const Card = ({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) => (
  <div className={`bg-white rounded-3xl shadow-sm border border-outline/5 ${className}`}>
    {children}
  </div>
);

const Dashboard = () => {
  const { classify, data, loading, error } = useClassify();

  return (
    <div className="min-h-screen bg-[#f5fbef] p-6 lg:p-10 font-sans text-on-surface">
      <main className="max-w-[1400px] mx-auto space-y-8">

        {/* ── Header + Form ── */}
        <section>
          <header className="mb-6">
            <h1 className="text-5xl font-black italic text-primary tracking-tighter">
              Waste <span className="text-on-surface">Finder.</span>
            </h1>
          </header>
          <ClassificationForm onScan={classify} loading={loading} />
        </section>

        {/* ── Row 1: Raw Analysis (full width) ── */}
        <section>
          <SectionLabel>Raw Analysis</SectionLabel>
          <Card className="p-4 min-h-[360px] flex items-center justify-center">
            {data ? (
              <ImageCanvas imageUrl={data.imageUrl} boxes={data.detectedObjects} />
            ) : (
              <div className="w-full h-[320px] flex items-center justify-center italic text-xs opacity-30 border-2 border-dashed border-primary/10 rounded-2xl">
                Waiting for image data...
              </div>
            )}
          </Card>
        </section>

        {/* ── Row 2: Detection Results · DSL Editor · Engine Info ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

          {/* Detection Results */}
          <div className="lg:col-span-5">
            <SectionLabel>Detection Results</SectionLabel>
            <Card className="p-5">
              {data?.result && (
                <p className="text-xs text-on-surface-variant mb-4 pb-3 border-b border-outline/10">
                  {data.result}
                </p>
              )}
              <MatchResult
                objects={data?.matchedObjects ?? []}
                status={loading ? "Scanning" : data ? "Success" : "Waiting"}
                error={error}
                queryAction={data?.queryAction}
              />
            </Card>
          </div>

          {/* DSL Editor */}
          <div className="lg:col-span-4">
            <SectionLabel>Generated DSL</SectionLabel>
            <div className="bg-[#1e1e1e] rounded-3xl overflow-hidden shadow-2xl border border-white/5">
              <div className="px-4 py-3 border-b border-white/10 flex justify-between items-center">
                <span className="text-[10px] font-bold text-white/40 uppercase tracking-widest">
                  Normalized Query
                </span>
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              </div>
              <div className="max-h-[260px] overflow-auto">
                <DSLEditor code={data?.dslCode ?? "// Waiting for input..."} />
              </div>
            </div>
          </div>

          {/* Engine Info */}
          <div className="lg:col-span-3">
            <SectionLabel>Engine Info</SectionLabel>
            <Card className="p-4">
              {data ? (
                <EngineInfo
                  engineUsed={data.engineUsed}
                  decisionReason={data.decisionReason}
                  primaryResult={data.primaryResult}
                  fallbackResult={data.fallbackResult}
                />
              ) : (
                <div className="flex items-center justify-center min-h-[120px] italic text-xs opacity-25">
                  Engine info will appear here
                </div>
              )}
            </Card>
          </div>
        </div>

        {/* ── Row 3: Token Stream (full width) ── */}
        <section>
          <SectionLabel>Token Stream</SectionLabel>
          <Card className="p-5">
            <TokenStream tokens={data?.tokens ?? []} />
          </Card>
        </section>

        {/* ── Row 4: Semantic AST · Formal Parse Tree ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <SectionLabel>Semantic AST</SectionLabel>
            <Card className="p-4 overflow-hidden">
              {data?.parseTree ? (
                <TreeVisualizer data={data.parseTree} />
              ) : (
                <div className="h-[380px] flex items-center justify-center text-xs italic opacity-20">
                  Semantic tree will render here
                </div>
              )}
            </Card>
          </div>

          <div>
            <SectionLabel>Formal Parse Tree (ANTLR CST)</SectionLabel>
            <Card className="p-4 overflow-hidden">
              {data?.formalParseTree ? (
                <TreeVisualizer data={data.formalParseTree} showTerminalText />
              ) : (
                <div className="h-[380px] flex items-center justify-center text-xs italic opacity-20">
                  Formal tree will render here
                </div>
              )}
            </Card>
          </div>
        </div>

      </main>
    </div>
  );
};

export default Dashboard;
