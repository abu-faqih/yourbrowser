package com.yourbrowser.app.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.yourbrowser.app.R
import com.yourbrowser.app.model.BrowserTab

class TabsBottomSheet(
    private val tabs: List<BrowserTab>,
    private val activeTabId: String,
    private val onTabSelected: (BrowserTab) -> Unit,
    private val onTabClosed: (BrowserTab) -> Unit,
    private val onNewTab: () -> Unit,
    private val onLockToggle: (BrowserTab) -> Unit
) : BottomSheetDialogFragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(R.layout.bottom_sheet_tabs, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recycler = view.findViewById<RecyclerView>(R.id.recycler_tabs)
        recycler.layoutManager = LinearLayoutManager(requireContext())
        val adapter = TabsAdapter(
            tabs = tabs,
            activeTabId = activeTabId,
            onTabSelected = {
                onTabSelected(it)
                dismiss()
            },
            onTabClosed = {
                onTabClosed(it)
                if (tabs.isEmpty()) {
                    dismiss()
                } else {
                    recycler.adapter?.notifyDataSetChanged()
                }
            },
            onLockToggle = {
                onLockToggle(it)
                recycler.adapter?.notifyDataSetChanged()
            }
        )
        recycler.adapter = adapter

        view.findViewById<Button>(R.id.btn_sheet_new_tab).setOnClickListener {
            onNewTab()
            dismiss()
        }
    }
}
