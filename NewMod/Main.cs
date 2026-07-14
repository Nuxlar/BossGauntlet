using BepInEx;
using RoR2.ContentManagement;
using System.Diagnostics;
using System.IO;
using UnityEngine;
using UnityEngine.AddressableAssets;

namespace NewMod
{
  [BepInPlugin(PluginGUID, PluginName, PluginVersion)]
  public class Main : BaseUnityPlugin
  {
    public const string PluginGUID = PluginAuthor + "." + PluginName;
    public const string PluginAuthor = "Nuxlar";
    public const string PluginName = "NewMod";
    public const string PluginVersion = "1.0.0";

    internal static Main Instance { get; private set; }
    public static string PluginDirectory { get; private set; }

    public static GameObject exampleVanillaAsset = Addressables.LoadAssetAsync<GameObject>(RoR2BepInExPack.GameAssetPaths.Version_1_39_0.RoR2_Base_Commando.CommandoBody_prefab).WaitForCompletion();

    public void Awake()
    {
      Instance = this;

      Log.Init(Logger);

      // PluginDirectory = Path.GetDirectoryName(Info.Location);
    }
  }
}