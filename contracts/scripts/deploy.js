const hre = require("hardhat");

async function main() {
  console.log("Deploying NEXUS Search contracts...");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  // Deploy NXS Token
  console.log("\nDeploying NXS Token...");
  const NXSToken = await hre.ethers.getContractFactory("NXSToken");
  
  // Use deployer address for all fund addresses (replace in production)
  const teamMultisig = deployer.address;
  const investorMultisig = deployer.address;
  const ecosystemFund = deployer.address;
  const rewardsPool = deployer.address;
  const liquidityPool = deployer.address;

  const nxsToken = await NXSToken.deploy(
    teamMultisig,
    investorMultisig,
    ecosystemFund,
    rewardsPool,
    liquidityPool
  );
  await nxsToken.waitForDeployment();
  console.log("NXS Token deployed to:", await nxsToken.getAddress());

  // Deploy Staking Contract
  console.log("\nDeploying Staking Contract...");
  const NXSStaking = await hre.ethers.getContractFactory("NXSStaking");
  const nxsStaking = await NXSStaking.deploy(
    await nxsToken.getAddress(),
    rewardsPool
  );
  await nxsStaking.waitForDeployment();
  console.log("NXS Staking deployed to:", await nxsStaking.getAddress());

  // Deploy Subscription NFT
  console.log("\nDeploying Subscription NFT...");
  const NXSSubscription = await hre.ethers.getContractFactory("NXSSubscription");
  const nxsSubscription = await NXSSubscription.deploy();
  await nxsSubscription.waitForDeployment();
  console.log("NXS Subscription deployed to:", await nxsSubscription.getAddress());

  // Log deployment info
  console.log("\n========================================");
  console.log("Deployment Summary");
  console.log("========================================");
  console.log("NXS Token:", await nxsToken.getAddress());
  console.log("NXS Staking:", await nxsStaking.getAddress());
  console.log("NXS Subscription:", await nxsSubscription.getAddress());
  console.log("========================================");

  // Verify contracts (if on public network)
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\nVerifying contracts...");
    try {
      await hre.run("verify:verify", {
        address: await nxsToken.getAddress(),
        constructorArguments: [
          teamMultisig,
          investorMultisig,
          ecosystemFund,
          rewardsPool,
          liquidityPool
        ]
      });
      console.log("NXS Token verified");
    } catch (e) {
      console.log("NXS Token verification failed:", e.message);
    }

    try {
      await hre.run("verify:verify", {
        address: await nxsStaking.getAddress(),
        constructorArguments: [
          await nxsToken.getAddress(),
          rewardsPool
        ]
      });
      console.log("NXS Staking verified");
    } catch (e) {
      console.log("NXS Staking verification failed:", e.message);
    }

    try {
      await hre.run("verify:verify", {
        address: await nxsSubscription.getAddress(),
        constructorArguments: []
      });
      console.log("NXS Subscription verified");
    } catch (e) {
      console.log("NXS Subscription verification failed:", e.message);
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
