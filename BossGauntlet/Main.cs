using System.Collections.Generic;
using BepInEx;
using RoR2;
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.Networking;
using Paths = RoR2BepInExPack.GameAssetPaths.Version_1_39_0;

namespace BossGauntlet
{
  [BepInPlugin(PluginGUID, PluginName, PluginVersion)]
  public class Main : BaseUnityPlugin
  {
    public const string PluginGUID = PluginAuthor + "." + PluginName;
    public const string PluginAuthor = "Nuxlar";
    public const string PluginName = "BossGauntlet";
    public const string PluginVersion = "1.0.0";

    private static (string sceneName, InteractableSpawnCard portalCard)[] portals =
    {
      ("moon2", Addressables.LoadAssetAsync<InteractableSpawnCard>(Paths.RoR2_Base_PortalMS.iscMSPortal_asset).WaitForCompletion()),
      ("voidraid", Addressables.LoadAssetAsync<InteractableSpawnCard>(Paths.RoR2_DLC1_DeepVoidPortal.iscDeepVoidPortal_asset).WaitForCompletion()),
      ("meridian", Addressables.LoadAssetAsync<InteractableSpawnCard>(Paths.RoR2_DLC2.iscColossusPortal_asset).WaitForCompletion()),
      ("solusweb", Addressables.LoadAssetAsync<InteractableSpawnCard>(Paths.RoR2_DLC3_EyePortal.iscEyePortal_asset).WaitForCompletion()),
    };

    private static readonly List<string> defeated = new List<string>();

    public void Awake()
    {
      Log.Init(Logger);

      Run.onRunStartGlobal += _ => defeated.Clear();

      // Mithrix
      On.EntityStates.Missions.BrotherEncounter.BossDeath.OnEnter += (orig, self) =>
      {
        orig(self);
        OnBossDefeated("moon2");
      };

      // Voidling 
      On.EntityStates.VoidRaidCrab.DeathState.OnEnter += (orig, self) =>
      {
        orig(self);
        OnBossDefeated("voidraid");
      };

      // False Son
      On.EntityStates.FalseSonBoss.BrokenCrystalDeathState.OnEnter += (orig, self) =>
      {
        orig(self);
        OnBossDefeated("meridian");
      };
      // Solus Wing/Heart
      On.EntityStates.SolusHeart.Death.SolusHeartDeathSequence.OnEnter += (orig, self) =>
      {
        orig(self);
        OnBossDefeated("solusweb");
      };
    }

    private static void OnBossDefeated(string sceneName)
    {
      if (!NetworkServer.active || defeated.Contains(sceneName))
        return;

      defeated.Add(sceneName);
      SpawnPortals(GetPortalCenter());
    }

    private static Vector3 GetPortalCenter()
    {
      foreach (PlayerCharacterMasterController player in PlayerCharacterMasterController.instances)
      {
        CharacterBody body = player.master ? player.master.GetBody() : null;
        if (body && body.healthComponent && body.healthComponent.alive)
          return body.corePosition;
      }
      return Vector3.zero;
    }

    private static void SpawnPortals(Vector3 center)
    {
      if (center == Vector3.zero)
      {
        Log.Warning("BossGauntlet: Failed to spawn portals, no player found");
        return;
      } 

      Xoroshiro128Plus rng = Run.instance.stageRng;

      foreach ((string sceneName, InteractableSpawnCard portalCard) in portals)
      {
        if (defeated.Contains(sceneName))
          continue;

        DirectorPlacementRule placement = new DirectorPlacementRule
        {
          placementMode = DirectorPlacementRule.PlacementMode.Approximate,
          minDistance = 10f,
          maxDistance = 40f,
          position = center,
        };
        GameObject portal = DirectorCore.instance.TrySpawnObject(new DirectorSpawnRequest(portalCard, placement, rng));

        if (!portal)
        {
          Log.Error($"Boss Gauntlet: Failed to spawn portal to {sceneName}");
          continue;
        }

        SceneExitController exit = portal.GetComponentInChildren<SceneExitController>();
        exit.useRunNextStageScene = false;
        exit.destinationScene = SceneCatalog.GetSceneDefFromSceneName(sceneName);
        Log.Info($"Boss Gauntlet: Spawned portal to {sceneName}");
      }
    }
  }
}
