import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type ImageColumnProps = BaseColumnProps & {
  imageWidth?: string | number;
  imageHeight?: string | number;
};

export function ImageColumn(props: ImageColumnProps) {
  const { imageWidth, imageHeight } = props;
  const cell = useCellContext();
  if (!cell.value) {
    return null;
  }
  return (
    <div>
      <img src={cell.value} width={imageWidth} height={imageHeight} alt="" />
    </div>
  );
}
