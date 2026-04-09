import Tree from 'react-d3-tree';

interface Props { data: any }

const TreeVisualizer = ({ data }: Props) => {
  return (
    <div className="h-[450px] w-full glass-panel rounded-3xl overflow-hidden border border-outline/10">
      <Tree 
        data={data}
        orientation="vertical"
        pathClassFunc={() => 'stroke-primary stroke-2'}
        nodeSize={{ x: 180, y: 120 }} // Khoảng cách giữa các node
        separation={{ siblings: 1.5, nonSiblings: 2 }}
        translate={{ x: 300, y: 50 }}
        // Tùy chỉnh hiển thị Node để trông chuyên nghiệp hơn
        renderCustomNodeElement={({ nodeDatum }) => (
          <g>
            <circle r="15" fill="var(--color-primary)" />
            <text fill="var(--color-on-surface)" strokeWidth="0.5" x="20" y="5" className="text-[12px] font-bold">
              {(nodeDatum as any).name}
            </text>
          </g>
        )}
      />
    </div>
  );
};

export default TreeVisualizer;