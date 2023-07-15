{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    python311
    poetry
    nodePackages_latest.pnpm
  ];

  shellHook = ''
    poetry env use python3.11
    poetry install
    pnpm install
  '';
}
