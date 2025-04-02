import { ReactNode } from "react";

type CardActionsProps = { children: ReactNode | ReactNode[] };

const CardActions = (props: CardActionsProps) => {
  return (
    <div className="mt-2 flex items-center justify-end gap-2 self-end">
      {props.children}
    </div>
  );
};

export default CardActions;
