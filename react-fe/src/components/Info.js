import { useSpring, animated, config } from "@react-spring/web";

export default function Info() {
  const [{ background }] = useSpring(
    () => ({
      from: { background: "#ffffff" },
      to: [
        { background: "#ffffff" },
        { background: "#efefef" },
        { background: "#dedede" },
        { background: "#c9c9c9" },
        { background: "#dedede" },
        { background: "#efefef" },
      ],
      config: config.molasses,
      loop: {
        reverse: true,
      },
    }),
    []
  );

  const CardClickNavigateOne = () => {
    window.open(
      "https://github.com/dbhatia00/documentation-generation/blob/main/README.md"
    );
  };

  const CardClickNavigateTwo = () => {
    window.open(
      "https://github.com/dbhatia00/documentation-generation/blob/main/documentation/Roles.md"
    );
  };

  const CardClickNavigateThree = () => {
    window.open("https://github.com/dbhatia00/documentation-generation/issues");
  };

  return (
    <div class="col-container">
      <animated.div
        class="card fixed-height mt-4 d-none d-md-block right-card"
        style={{ background }}
        onClick={CardClickNavigateOne}
      >
        <div class="card-body">
          <h5 class="card-title">Documentation Generation</h5>
          <h6 class="card-subtitle mb-2 text-body-secondary">
            Learn more about our project
          </h6>
          <p class="card-text">Take a look at our README!</p>
        </div>
      </animated.div>
      <animated.div
        class="card fixed-height mt-4 d-none d-md-block right-card"
        style={{ background }}
        onClick={CardClickNavigateTwo}
      >
        <div class="card-body">
          <h5 class="card-title">About Us</h5>
          <h6 class="card-subtitle mb-2 text-body-secondary">
            Learn more about our team
          </h6>
          <p class="card-text">Take a look at our contributors!</p>
        </div>
      </animated.div>
      <animated.div
        class="card fixed-height mt-4 d-none d-md-block right-card"
        style={{ background }}
        onClick={CardClickNavigateThree}
      >
        <div class="card-body">
          <h5 class="card-title">Looking Forward</h5>
          <h6 class="card-subtitle mb-2 text-body-secondary">
            Learn more about future works
          </h6>
          <p class="card-text">Take a look at our open issues!</p>
        </div>
      </animated.div>
    </div>
  );
}
