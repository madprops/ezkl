{
  description = "ezkl - jump to directories";

  # This pulls in the standard Nix package collection
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  # This defines what your repository provides when someone uses it
  outputs = { self, nixpkgs }:
    let
      # Define the architectures you want to support (Linux & Mac)
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # A helper to generate the package for all supported systems
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      # 1. The Package Definition
      packages = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };

          # Bundle your dependencies here
          myPythonEnv = pkgs.python3.withPackages (ps: with ps; [
            # requests
            # pyyaml
          ]);
        in
        {
          default = pkgs.stdenv.mkDerivation {
            pname = "ezkl";
            version = "main"; # Or use self.shortRev to use the git commit hash

            # Crucial: This tells Nix to use the current repository as the source
            src = ./.;

            nativeBuildInputs = [ pkgs.makeWrapper ];

            installPhase = ''
              mkdir -p $out/bin
              mkdir -p $out/libexec/ezkl

              cp -r . $out/libexec/ezkl/

              makeWrapper ${myPythonEnv}/bin/python3 $out/bin/ezkl \
                --add-flags "$out/libexec/ezkl/ezkl.py"
            '';
          };
        }
      );

      # 2. The App Definition (makes `nix run` work seamlessly)
      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/ezkl";
        };
      });
    };
}