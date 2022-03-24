{
  description = "flake for camillescott.github.io";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };
      ws-gems = pkgs.bundlerEnv {
        name = "ws-gems";
        inherit (pkgs.ruby);
        gemdir = ./.;
      };
      ws = pkgs.stdenv.mkDerivation {
        name = "ws";
        src = self;
        buildPhase = ''
          bundle exec jekyll build
        '';
        installPhase = ''
          cp -r _site/. $out
        '';
        buildInputs = [
          ws-gems
          pkgs.ruby
        ];
      };
      ws-host = pkgs.writeShellScriptBin "ws-host" ''
        cd ${ws}
        ${pkgs.ruby}/bin/ruby -run -e httpd -- .
      '';
    in
    {
      packages = flake-utils.lib.flattenTree {
        inherit ws;
      };
      defaultPackage = self.packages.${system}.ws;
      apps = {
        ws-host = flake-utils.lib.mkApp { 
          drv = ws-host;
        };
      };
      defaultApp = self.apps.${system}.ws-host;
      devShell = pkgs.mkShell {
        buildInputs = ws.buildInputs ++ [
          pkgs.bundix
        ];
      };
    }
  );
}

