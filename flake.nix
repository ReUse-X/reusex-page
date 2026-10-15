{
  description = "ReUseX";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    flake-utils.url = "github:numtide/flake-utils";

    pre-commit-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  }; # end of inputs

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    pre-commit-hooks,
  }:
    flake-utils.lib.eachSystem ["x86_64-linux"] (
      system:
      # flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (nixpkgs) lib;

        # Import nixpkgs with custom configurations and overlays
        pkgs = import nixpkgs {
          inherit system;

          # Set systm comfigurations such as CUDA support and unfree packages
          config = {
            cudaSupport = true;
            hardware.nvidia.open = false;
            allowUnfree = true;
          };

          # Set overlays and custom fixes for broken packages
          #overlays = import ./overlays { inherit lib; };
        };
      in {
        formatter = pkgs.alejandra;

        checks.pre-commit-check = pre-commit-hooks.lib.${system}.run {
          src = ./.;
          default_stages = ["pre-commit"];
          hooks = {
            check-added-large-files.enable = true;
            check-case-conflicts.enable = true;
            check-executables-have-shebangs.enable = true;
            check-shebang-scripts-are-executable.enable = true;
            check-merge-conflicts.enable = true;
            alejandra.enable = true;
            #reuse = {
            #  enable = true;
            #};
          };
        };

        #packages = {
        #  #  default = pkgs.ReUseX; # ReUseX
        #  #  rtabmap = pkgs.rtabmap;
        #}
        ## All custom packages
        #// (pkgs.lib.packagesFromDirectoryRecursive {
        #  callPackage = pkgs.lib.callPackageWith pkgs;
        #  directory = ./pkgs;
        #}); # end of packages

        devShells = {
          default = pkgs.mkShell {
            #inputsFrom = [ self.packages.${system}.default ];
            buildInputs = self.checks.${system}.pre-commit-check.enabledPackages;

            packages = with pkgs; [
              # DevOps tools
              nix-update
              github-copilot-cli
              hugo
              tailwindcss_4
              claude-code

              # Issue tracking (bd)
              beads

              # Design loop: headless screenshots of the live `hugo server`
              # (.claude/skills/design-studio/scripts/shot.py)
              (python3.withPackages (ps: [ps.playwright]))
              playwright-driver.browsers-chromium
            ];

            # Point Python Playwright at the Nix-provided browsers (no `playwright install`).
            PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers-chromium}";
            PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = "true";

            shellHook =
              ''
                echo "Entering dev shell"
                export VIRTUAL_ENV_PROMPT="ReUseX Webpage"
              ''
              + self.checks.${system}.pre-commit-check.shellHook;
          }; # end of default shell

          # Minimal shell for CI: build + checks only (no browsers, no CLIs).
          ci = pkgs.mkShell {
            packages = with pkgs; [
              hugo
              tailwindcss_4
              python3
              lychee
            ];
          };
        }; # end of devShells
      }
    ); # end of outputs
}
