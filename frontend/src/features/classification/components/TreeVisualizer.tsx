import Tree from "react-d3-tree";
import type { RawNodeDatum } from "react-d3-tree";

import type { WasteQueryTreeNodeResponse } from "../../../types/waste";

interface Props {
  data: WasteQueryTreeNodeResponse;
  showTerminalText?: boolean;
}

const TreeVisualizer = ({ data, showTerminalText = false }: Props) => {
  return (
    <div className="h-[380px] w-full glass-panel rounded-3xl overflow-hidden border border-outline/10">
      <Tree
        data={data as unknown as RawNodeDatum}
        orientation="vertical"
        pathClassFunc={() => "stroke-primary stroke-2"}
        nodeSize={{ x: 160, y: 110 }}
        separation={{ siblings: 1.5, nonSiblings: 2 }}
        translate={{ x: 260, y: 50 }}
        renderCustomNodeElement={({ nodeDatum }) => {
          const nodeData = nodeDatum as unknown as WasteQueryTreeNodeResponse;
          const isTerminal = nodeData.is_terminal;
          const termText = nodeData.text;
          const fillColor = isTerminal
            ? "var(--color-primary-container)"
            : "var(--color-primary)";

          return (
            <g>
              <circle r="13" fill={fillColor} />
              <text
                fill="var(--color-on-surface)"
                strokeWidth="0"
                x="18"
                y={showTerminalText && isTerminal && termText ? "-3" : "5"}
                style={{ fontSize: "11px", fontWeight: 700 }}
              >
                {nodeDatum.name}
              </text>
              {showTerminalText && isTerminal && termText && (
                <text
                  fill="var(--color-on-surface-variant)"
                  strokeWidth="0"
                  x="18"
                  y="11"
                  style={{ fontSize: "10px", fontFamily: "monospace" }}
                >
                  "{termText}"
                </text>
              )}
            </g>
          );
        }}
      />
    </div>
  );
};

export default TreeVisualizer;
