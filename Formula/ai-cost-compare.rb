class AiCostCompare < Formula
  include Language::Python::Virtualenv

  desc "Daily AI cost analysis (Claude Code, Cursor) with before/after comparison"
  homepage "https://github.com/mazulo/ai-cost-compare"
  url "https://files.pythonhosted.org/packages/5d/f4/1adce4384f0cd25285942c8f2c40ee12774a0b57ac7941ffbb1b882c1f95/ai_cost_compare-0.3.2.tar.gz"
  sha256 "bc6da1afb0a53c64b70ce86702e10aa6f721167ea8e6671befb5528b68f71b15"
  license "MIT"

  depends_on "node"
  depends_on "python@3.13"

  resource "attrs" do
    url "https://files.pythonhosted.org/packages/9a/8e/82a0fe20a541c03148528be8cac2408564a6c9a0cc7e9171802bc1d26985/attrs-26.1.0.tar.gz"
    sha256 "d03ceb89cb322a8fd706d4fb91940737b6642aa36998fe130a9bc96c985eff32"
  end

  resource "cyclopts" do
    url "https://files.pythonhosted.org/packages/9a/19/5c438b428b3dca208eb920804dc16aeb3ca1e85d6163d17e8fb0785ead19/cyclopts-4.18.0.tar.gz"
    sha256 "fb7b730f21932e0784f7e54462df0447aaa1fbf034d65b605bd8a25dce58b188"
  end

  resource "docstring-parser" do
    url "https://files.pythonhosted.org/packages/e0/4d/f332313098c1de1b2d2ff91cf2674415cc7cddab2ca1b01ae29774bd5fdf/docstring_parser-0.18.0.tar.gz"
    sha256 "292510982205c12b1248696f44959db3cdd1740237a968ea1e2e7a900eeb2015"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/06/ff/7841249c247aa650a76b9ee4bbaeae59370dc8bfd2f6c01f3630c35eb134/markdown_it_py-4.2.0.tar.gz"
    sha256 "04a21681d6fbb623de53f6f364d352309d4094dd4194040a10fd51833e418d49"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3efefba235e65cdeb9c84d24a8293ba1d90/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/c3/b2/bc9c9196916376152d655522fdcebac55e66de6603a76a02bca1b6414f6c/pygments-2.20.0.tar.gz"
    sha256 "6757cd03768053ff99f3039c1a36d6c0aa0b263438fcab17520b30a303a82b5f"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/c0/8f/0722ca900cc807c13a6a0c696dacf35430f72e0ec571c4275d2371fca3e9/rich-15.0.0.tar.gz"
    sha256 "edd07a4824c6b40189fb7ac9bc4c52536e9780fbbfbddf6f1e2502c31b068c36"
  end

  resource "rich-rst" do
    url "https://files.pythonhosted.org/packages/57/56/3191bae66b08ccc637ea8120426068bcb361cc323c96404c310886937067/rich_rst-2.0.1.tar.gz"
    sha256 "cbe236ed0901d1ec8427cc6a50bf0a34353ba28ad014dc24def68bfe7f3b9e68"
  end
  def install
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      ai-cost-compare reads usage data via ccusage. Install it with:

        npm install -g ccusage
    EOS
  end

  test do
    assert_match "Daily Claude cost analysis", shell_output("#{bin}/ai-cost-compare --help")
  end
end
