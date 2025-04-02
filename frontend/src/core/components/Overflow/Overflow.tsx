import clsx from "clsx";
import { forwardRef, useEffect, useRef, useState } from "react";

type OverflowProps = {
  fromColor?: string;
  horizontal?: boolean;
  gradientWidth?: string;
  gradientHeight?: string;
  vertical?: boolean;
  forwardedRef?: React.RefObject<HTMLDivElement>;
} & React.HTMLAttributes<HTMLDivElement>;

enum OverflowY {
  NONE,
  TOP,
  BOTTOM,
  BOTH,
}

enum OverflowX {
  NONE,
  LEFT,
  RIGHT,
  BOTH,
}

function getVerticalOverflow(parent: HTMLDivElement, child: HTMLDivElement) {
  if (child.clientHeight <= parent.clientHeight) {
    return OverflowY.NONE;
  }
  const topOverflow = parent.scrollTop !== 0;
  const bottomOverflow =
    parent.scrollTop + parent.offsetHeight < child.offsetHeight;
  if (topOverflow && bottomOverflow) {
    return OverflowY.BOTH;
  } else if (topOverflow) {
    return OverflowY.TOP;
  } else if (bottomOverflow) {
    return OverflowY.BOTTOM;
  }

  return OverflowY.NONE;
}

function getHorizontalOverflow(parent: HTMLDivElement, child: HTMLDivElement) {
  if (child.scrollWidth <= parent.clientWidth) {
    return OverflowX.NONE;
  }
  const leftOverflow = parent.scrollLeft !== 0;
  const rightOverflow =
    parent.scrollLeft <
    child.offsetLeft + child.scrollWidth - parent.clientWidth;

  if (leftOverflow && rightOverflow) {
    return OverflowX.BOTH;
  } else if (leftOverflow) {
    return OverflowX.LEFT;
  } else if (rightOverflow) {
    return OverflowX.RIGHT;
  }

  return OverflowX.NONE;
}

const Overflow = forwardRef(function (props: OverflowProps, ref) {
  const {
    children,
    className,
    fromColor = "from-white",
    horizontal = false,
    vertical = false,
    gradientWidth = "w-6",
    gradientHeight = "h-6",
    forwardedRef,
    ...delegated
  } = props;

  const parentRef = useRef<HTMLDivElement>(null);
  const _childRef = useRef<HTMLDivElement>(null);
  const [overflowY, setOverflowY] = useState<OverflowY>(OverflowY.NONE);
  const [overflowX, setOverflowX] = useState<OverflowX>(OverflowX.NONE);

  const childRef = forwardedRef ?? _childRef;

  useEffect(() => {
    // Listen for scroll
    if (!parentRef.current || !childRef.current) {
      return;
    }

    if (!vertical) {
      setOverflowY(OverflowY.NONE);
    }
    if (!horizontal) {
      setOverflowX(OverflowX.NONE);
    }

    const parent = parentRef.current;
    const child = childRef.current;
    const handleScroll = () => {
      if (!parent || !child) return;
      if (vertical) {
        setOverflowY(getVerticalOverflow(parent, child));
      }
      if (horizontal) {
        setOverflowX(getHorizontalOverflow(parent, child));
      }
    };
    parent.addEventListener("scroll", handleScroll);

    // Initial check
    handleScroll();

    return () => {
      parent.removeEventListener("scroll", handleScroll);
    };
  }, [overflowY, overflowX, childRef, parentRef, vertical, horizontal]);

  return (
    <div className={clsx("relative", className)}>
      <div
        {...delegated}
        ref={parentRef}
        className={clsx(
          "h-full",
          horizontal && "overflow-x-auto",
          vertical && "overflow-y-auto",
        )}
      >
        {vertical && (
          <div
            className={clsx(
              "pointer-events-none absolute top-0 w-full bg-linear-to-b to-transparent transition-opacity duration-100",
              fromColor,
              gradientHeight,
              ![OverflowY.BOTH, OverflowY.TOP].includes(overflowY) &&
                "opacity-0",
            )}
          ></div>
        )}
        {horizontal && (
          <div
            className={clsx(
              "pointer-events-none absolute bottom-0 left-0 top-0 bg-linear-to-r to-transparent transition-opacity duration-100",
              fromColor,
              gradientWidth,
              ![OverflowX.BOTH, OverflowX.LEFT].includes(overflowX) &&
                "opacity-0",
            )}
          ></div>
        )}
        <div id="child" ref={childRef}>
          {children}
        </div>
        {horizontal && (
          <div
            className={clsx(
              "pointer-events-none absolute bottom-0 right-0 top-0 bg-linear-to-l to-transparent transition-opacity duration-100",
              fromColor,
              gradientWidth,
              ![OverflowX.BOTH, OverflowX.RIGHT].includes(overflowX) &&
                "opacity-0",
            )}
          ></div>
        )}
        {vertical && (
          <div
            className={clsx(
              "pointer-events-none absolute bottom-0 w-full bg-linear-to-t to-transparent transition-opacity duration-100",
              fromColor,
              gradientHeight,
              ![OverflowY.BOTH, OverflowY.BOTTOM].includes(overflowY) &&
                "opacity-0",
            )}
          ></div>
        )}
      </div>
    </div>
  );
});

export default Overflow;
