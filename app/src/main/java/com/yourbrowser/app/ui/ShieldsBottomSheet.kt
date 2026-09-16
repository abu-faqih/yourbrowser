package com.yourbrowser.app.ui

import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.switchmaterial.SwitchMaterial
import com.yourbrowser.app.R
import com.yourbrowser.app.core.BraveShieldsInterceptor

class ShieldsBottomSheet(
    private val interceptor: BraveShieldsInterceptor,
    private val currentUrl: String,
    private val onShieldsToggled: (Boolean) -> Unit
) : BottomSheetDialogFragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(R.layout.bottom_sheet_shields, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val switchShields = view.findViewById<SwitchMaterial>(R.id.switch_shields)
        val txtDomain = view.findViewById<TextView>(R.id.txt_shields_domain)
        val txtCount = view.findViewById<TextView>(R.id.txt_metric_count)

        val host = try { Uri.parse(currentUrl).host ?: "current site" } catch (e: Exception) { "current site" }
        txtDomain.text = "Protections for $host"
        txtCount.text = interceptor.getBlockedCount().toString()

        switchShields.isChecked = interceptor.shieldsEnabled
        switchShields.setOnCheckedChangeListener { _, isChecked ->
            interceptor.shieldsEnabled = isChecked
            onShieldsToggled(isChecked)
        }
    }
}
