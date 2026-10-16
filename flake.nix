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
            # Binary media goes to Git LFS (.gitattributes); LFS files are
            # skipped by this check, so the 500 KB default stays.
            check-added-large-files.enable = true;
            check-case-conflicts.enable = true;
            check-executables-have-shebangs.enable = true;
            check-shebang-scripts-are-executable.enable = true;
            check-merge-conflicts.enable = true;
            alejandra.enable = true;

            # Git LFS, run as pre-commit stages so they live in the same hook
            # files as everything else (and beads adds its sections there).
            # pre-commit consumes git's pre-push stdin itself, so the ref line
            # `git lfs pre-push` needs is rebuilt from pre-commit's variables —
            # without it git-lfs gets no refs and uploads nothing.
            git-lfs-pre-push = {
              enable = true;
              name = "git-lfs pre-push";
              entry = "${pkgs.writeShellScript "git-lfs-pre-push" ''
                local_ref="''${PRE_COMMIT_LOCAL_BRANCH:-HEAD}"
                local_sha="''${PRE_COMMIT_TO_REF:-$(${pkgs.git}/bin/git rev-parse "$local_ref")}"
                remote_ref="''${PRE_COMMIT_REMOTE_BRANCH:-$local_ref}"
                remote_sha="''${PRE_COMMIT_FROM_REF:-0000000000000000000000000000000000000000}"
                printf '%s %s %s %s\n' "$local_ref" "$local_sha" "$remote_ref" "$remote_sha" |
                  exec ${pkgs.git-lfs}/bin/git-lfs pre-push "$PRE_COMMIT_REMOTE_NAME" "$PRE_COMMIT_REMOTE_URL"
              ''}";
              stages = ["pre-push"];
              pass_filenames = false;
              always_run = true;
            };
            git-lfs-post-checkout = {
              enable = true;
              name = "git-lfs post-checkout";
              entry = "${pkgs.writeShellScript "git-lfs-post-checkout" ''
                exec ${pkgs.git-lfs}/bin/git-lfs post-checkout "$PRE_COMMIT_FROM_REF" "$PRE_COMMIT_TO_REF" "$PRE_COMMIT_CHECKOUT_TYPE"
              ''}";
              stages = ["post-checkout"];
              pass_filenames = false;
              always_run = true;
            };
            git-lfs-post-merge = {
              enable = true;
              name = "git-lfs post-merge";
              entry = "${pkgs.writeShellScript "git-lfs-post-merge" ''
                exec ${pkgs.git-lfs}/bin/git-lfs post-merge "$PRE_COMMIT_IS_SQUASH_MERGE"
              ''}";
              stages = ["post-merge"];
              pass_filenames = false;
              always_run = true;
            };
            git-lfs-post-commit = {
              enable = true;
              name = "git-lfs post-commit";
              entry = "${pkgs.git-lfs}/bin/git-lfs post-commit";
              stages = ["post-commit"];
              pass_filenames = false;
              always_run = true;
            };
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

              # Binary media (images, video) is stored in Git LFS
              git-lfs

              # Design loop: headless screenshots of the live `hugo server`
              # (.claude/skills/design-studio/scripts/shot.py)
              (python3.withPackages (ps: [ps.playwright]))
              playwright-driver.browsers-chromium

              # Media pipeline (app-capture, infographics, media-library skills):
              # encode frame sequences, derive web video/stills, contact sheets.
              ffmpeg-headless
            ];

            # Point Python Playwright at the Nix-provided browsers (no `playwright install`).
            PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers-chromium}";
            PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = "true";

            shellHook =
              ''
                echo "Entering dev shell"
                export VIRTUAL_ENV_PROMPT="ReUseX Webpage"
              ''
              # Installs the pre-commit stages (incl. the git-lfs hooks) into
              # .git/hooks when the hook config changed; clears core.hooksPath.
              + self.checks.${system}.pre-commit-check.shellHook
              + ''
                if git rev-parse --git-dir >/dev/null 2>&1; then
                  # LFS clean/smudge filters for this clone (hooks come from above).
                  git lfs install --local --skip-repo >/dev/null
                  # Beads adds its sections to the same hook files (idempotent;
                  # needed again after git-hooks.nix rewrote them).
                  git config --local --unset-all core.hooksPath 2>/dev/null || true
                  bd hooks install >/dev/null 2>&1 || echo 1>&2 "dev shell: bd hooks install failed"
                fi
              '';
          }; # end of default shell

          # Minimal shell for CI: build + checks only (no browsers, no CLIs).
          ci = pkgs.mkShell {
            packages = with pkgs; [
              git-lfs
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
