import type { TokenInfoResponse } from "../../../types/waste";

interface Props {
  tokens: TokenInfoResponse[];
}

const TOKEN_STYLES: Record<string, string> = {
  FIND:        "bg-blue-100 text-blue-800 border-blue-200",
  COUNT:       "bg-purple-100 text-purple-800 border-purple-200",
  ME:          "bg-gray-100 text-gray-500 border-gray-200",
  WASTE:       "bg-gray-100 text-gray-500 border-gray-200",
  WHERE:       "bg-orange-100 text-orange-800 border-orange-200",
  AND:         "bg-orange-100 text-orange-800 border-orange-200",
  CONFIDENCE:  "bg-green-100 text-green-800 border-green-200",
  LABEL:       "bg-green-100 text-green-800 border-green-200",
  ORGANIC:     "bg-emerald-100 text-emerald-800 border-emerald-200",
  RECYCLABLE:  "bg-cyan-100 text-cyan-800 border-cyan-200",
  INORGANIC:   "bg-slate-100 text-slate-700 border-slate-200",
  GTE:         "bg-yellow-100 text-yellow-800 border-yellow-200",
  GT:          "bg-yellow-100 text-yellow-800 border-yellow-200",
  LTE:         "bg-yellow-100 text-yellow-800 border-yellow-200",
  LT:          "bg-yellow-100 text-yellow-800 border-yellow-200",
  EQ:          "bg-yellow-100 text-yellow-800 border-yellow-200",
  ASSIGN:      "bg-yellow-100 text-yellow-800 border-yellow-200",
  DECIMAL:     "bg-pink-100 text-pink-800 border-pink-200",
  STRING:      "bg-rose-100 text-rose-800 border-rose-200",
  IDENTIFIER:  "bg-indigo-100 text-indigo-800 border-indigo-200",
};

const TokenStream = ({ tokens }: Props) => {
  if (!tokens.length) {
    return (
      <div className="flex items-center justify-center h-14 text-xs italic opacity-25">
        Token stream will appear here after a scan
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2 items-start">
      {tokens.map((token, i) => {
        const style = TOKEN_STYLES[token.type] ?? "bg-gray-100 text-gray-600 border-gray-200";
        return (
          <div
            key={i}
            className={`flex flex-col items-center rounded-xl border px-3 py-2 min-w-[52px] ${style}`}
          >
            <span className="text-[8px] font-bold uppercase tracking-wider opacity-60 leading-none mb-1">
              {token.type}
            </span>
            <span className="text-[13px] font-mono font-semibold leading-none">
              {token.text}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default TokenStream;
