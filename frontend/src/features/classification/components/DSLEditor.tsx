interface Props { code: string }
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import pascal from 'react-syntax-highlighter/dist/esm/languages/prism/pascal';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';

SyntaxHighlighter.registerLanguage('pascal', pascal);

const DSLEditor = ({ code }: Props) => {
  return (
    <div className="bg-[#1e1e1e] rounded-3xl p-6 h-full border border-white/5 flex flex-col shadow-inner">
      <div className="flex items-center justify-between mb-4 text-xs font-mono text-white/40 uppercase tracking-widest">
        <span>Generated DSL Code</span>
        <button onClick={() => navigator.clipboard.writeText(code)} className="hover:text-primary transition-colors">
          <span className="material-symbols-outlined text-sm">content_copy</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-auto custom-scrollbar">
        <SyntaxHighlighter 
          language="pascal" // Hoặc bất kỳ ngôn ngữ nào gần giống DSL của bạn
          style={dracula}
          customStyle={{ background: 'transparent', fontSize: '12px', lineHeight: '1.6' }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

export default DSLEditor;